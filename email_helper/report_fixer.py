import os
import tarfile
import tempfile


def traverse(root_path, final=True):
    for path, dirs, files in os.walk(root_path):
        if path[-1].isdigit() and files:
            task = Try = user = report = ""
            for frag in path.split(os.path.sep):
                if frag[:2].isdigit() and frag[2:3] == "_":
                    task = frag
                elif frag.isdigit():
                    Try = frag
                elif "@" in frag:
                    user = frag
            for name in files:
                if name.endswith(".png"):
                    continue
                report = name.split(".")[-1].rstrip("_")
                file = os.path.join(path, name)
                if final == name.endswith("_"):
                    yield file, user, task, Try, report


def is_tar(btext):
    f = tempfile.NamedTemporaryFile()
    f.write(btext)
    f.flush()
    try:
        tarfile.is_tarfile(f) and tarfile.open(f.name).getmembers()
    except Exception:
        return False
    return True


def report_fixer(root_path):
    for file, *tail in traverse(root_path, final=False):
        with open(file, "rb") as f:
            content = f.read()
        while not is_tar(content):
            if (i := content.find(b"login: ")) > -1:
                content = content[i + 7:]
                continue
            if b'\r\n' in content:
                content = content.replace(b'\r\n', b'\n')
                continue
            break
        else:
            with open(file, "wb") as f:
                f.write(content)
            continue
