import errno
import glob
import os
import re
import shutil
import stat
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from fnmatch import fnmatch
from os.path import exists, isdir, isfile
from os.path import join as j
from zipfile import ZIP_DEFLATED, ZipFile

from py_tools import logger
from py_tools.common import retry as retry_dec
from py_tools.common import short_md5


@contextmanager
def working_dir(p, force_create=False, finally_remove=False, create_empty=False):
    """
    :param p: path to directory
    :param force_create: create if doesn't exists
    :param finally_remove: remove directory when exit
    :param create_empty: removes dir if already exists and creates new
    """
    cwd = os.getcwd()
    if create_empty and exists(p):
        shutil.rmtree(p)
    if force_create or create_empty:
        if not exists(p):
            os.makedirs(p)
    try:
        os.chdir(p)
    except:
        logger.error('failed to change dir', path=p, path2=cwd)
        raise

    try:
        yield
    finally:
        os.chdir(cwd)
        if finally_remove:
            shutil.rmtree(p)


def handle_remove_readonly(func, path, exc):
    exc_class, exc_value, tb = exc
    if func in (os.rmdir, os.remove, os.unlink) and exc_value.errno == errno.EACCES:
        # 0777 + remove readonly flag
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO | stat.S_IWRITE)
        func(path)
    elif (
        func in (os.rmdir, os.remove, os.listdir, os.unlink)
        and exc_value.errno == errno.ENOENT
    ):
        logger.info(
            "Tried to {} `{}', but path does not exists".format(func.__name__, path)
        )
    else:
        logger.info(
            'Error in func {} with errno {}'.format(func.__name__, exc_value.errno)
        )
        raise exc_class(str(exc_value) + str(exc_value.errno)).with_traceback(tb)
        # raise exc_value


def walk_files(
    root, patterns='*', antipatterns='', recursive=True, yield_folders=False
):
    """
    Yield all files and optionally folders from directory
    :param root: folder to walk
    :param patterns: unix shell style pattern of ';'-separated patterns. Yield only files that matched
    :param antipatterns: Yield only filels that not not matched
    :param recursive: walk into subdirs
    :param yield_folders: yield folders
    :return:
    """
    patterns = patterns.split(';')
    antipatterns = antipatterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            if any(fnmatch(name, p) for p in patterns) and not any(
                fnmatch(name, p) for p in antipatterns
            ):
                yield os.path.join(path, name)
        if not recursive:
            break


def zip_dir(src, name=None):
    assert os.path.isdir(src), '{} is expected to be a directory'.format(src)
    f_name = (name or os.path.basename(src)) + '.zip'
    with ZipFile(f_name, 'w', ZIP_DEFLATED) as f:
        with working_dir(src):
            for fn in walk_files('.'):
                f.write(fn)
    return f_name


def unzip_dir(f_name, dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name, ignore_errors=False, onerror=handle_remove_readonly)
    logger.info("extracting zip file `{}'".format(f_name))
    with ZipFile(f_name) as zip_file:
        os.makedirs(dir_name)
        zip_file.extractall(dir_name)


def safe_create_dir(dir_name):
    if os.path.isfile(dir_name):
        os.unlink(dir_name)
        logger.error('Found file when created such dir', path=dir_name)
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


def empty_dir(dir_name, ignore_errors=False):
    with working_dir(dir_name):
        for name in os.listdir('.'):
            if os.path.isfile(name):
                rm = os.unlink
            else:
                rm = shutil.rmtree
            if ignore_errors:
                try:
                    rm(name)
                except Exception:
                    pass
            else:
                rm(name)


def copy_tree(src, dst):
    """
    :param src: source folder
    :param dst: destination folder
    :return: list of copied files
    """
    if not isdir(dst):
        os.mkdir(dst)
    for p in os.listdir(src):
        if isfile(j(src, p)):
            shutil.copy(j(src, p), j(dst, p))
        elif isdir(j(src, p)):
            copy_tree(j(src, p), j(dst, p))
        else:
            # A workaround. Some fiels on share are not recognized as files by os.path.isfile
            #  but they still need to be copied
            try:
                shutil.copy(j(src, p), j(dst, p))
            except:
                copy_tree(j(src, p), j(dst, p))


def file_exists(p):
    """
    os.path.exists doesn't work for files on network path in frozen python
    """
    try:
        open(p).close()
    except (IOError, WindowsError):
        return False
    return True


def delete_dir(dir_path, onerror='raise', retry=True):
    if retry:
        onerror_f = retry_dec(n=3, sleep=5)(handle_remove_readonly)
    else:
        onerror_f = handle_remove_readonly
    parent, dir_name = os.path.split(dir_path)
    tmp_name = 'to_delete_' + short_md5(dir_name + str(time.time()))
    with working_dir(parent or '.'):
        try:
            shutil.move(dir_name, tmp_name)
        except (WindowsError, IOError) as e:
            if onerror == 'raise':
                raise e
            elif onerror == 'log':
                logger.info('Cannot delete folder', paht=dir_path, error=e)
            elif onerror == 'ignore':
                pass
            else:
                raise TypeError('unknown mode: {}'.format(onerror))
        else:
            try:
                shutil.rmtree(tmp_name, ignore_errors=False, onerror=onerror_f)
            except (WindowsError, IOError) as e:
                if onerror == 'raise':
                    raise e
                elif onerror == 'log':
                    logger.info('Cannot delete folder', path=dir_path, error=e)
                elif onerror == 'ignore':
                    pass
                else:
                    raise TypeError('unknown mode: {}'.format(onerror))


def file_older_then(f, tm):
    time_delta = datetime.now() - timedelta(seconds=tm)
    try:
        filetime = datetime.fromtimestamp(os.path.getctime(f))

        if filetime < time_delta:
            return True
        return False
    except WindowsError:
        print("Can't find file: {}".format(f))
        return False


def fix_filename(f_name):
    res = f_name.strip(' \n\r')
    replace_map = {
        '_': r'#$%\/\\ *&:+|=',
        '': r'?!"`' + "'",
        '(': r'{<',
        ')': r'}>',
    }
    for replacement, chars in replace_map.items():
        res = re.sub('[' + chars + ']', replacement, res)
    return res


def increment_file_name(f_name):
    """
    Add suffix to the TXT filename to avoid overwriting
     AF.txt -> AF_1.txt ... if AF_1.txt exists than AF_2.txt
    and so on
    """
    name, ext = os.path.splitext(f_name)
    counter = 0
    for f_name in glob.glob(name + '*' + ext):
        match = re.search(r'.*_(\d+){}'.format(re.escape(ext)), f_name)
        if match:
            counter = max(counter, int(match.group(1)))

    return '{}_{}{}'.format(name, counter + 1, ext)


def increment_file_name_2(f_name):
    """
    returns f_name with added or incremented suffix if f_name exists.
    :param f_name:
    :return:
    """

    def split_f_name(f_name):
        m = re.match(r'^(.+?)(_(\d+))?(\.(.+))??$', f_name)
        return m.group(1), int(m.group(3) or 0), m.group(5)

    def join_f_name(name, suffix, ext):
        if not ext:
            return '{}_{}'.format(name, suffix)
        return '{}_{}.{}'.format(name, suffix, ext)

    dirname = os.path.dirname(f_name) or '.'

    if not os.path.exists(dirname):
        return f_name

    name, suffix, ext = split_f_name(os.path.basename(f_name))

    with working_dir(dirname):
        while os.path.exists(join_f_name(name, suffix, ext)):
            suffix += 1
        return j(dirname, join_f_name(name, suffix, ext))


def increment_file_name_3(f_name):
    """
    returns f_name with added or incremented suffix. Doesnt't takes into an account real state of a files
    :param f_name:
    :return:
    """

    def split_f_name(f_name):
        m = re.match(r'^(.+?)(_(\d+))?(\.(.+))??$', f_name)
        return m.group(1), int(m.group(3) or 0), m.group(5)

    def join_f_name(name, suffix, ext):
        if not ext:
            return '{}_{}'.format(name, suffix)
        return '{}_{}.{}'.format(name, suffix, ext)

    dirname = os.path.dirname(f_name)
    name, suffix, ext = split_f_name(os.path.basename(f_name))
    if dirname:
        return j(dirname, join_f_name(name, suffix + 1, ext))
    else:
        return join_f_name(name, suffix + 1, ext)
