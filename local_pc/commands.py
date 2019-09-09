import os


def successJson(success: bool) -> dict:
    return {"success": success}



def list_dir(args: list) -> list:
    
    fileToJson = lambda file: {
        "name": file.name,
        "is_dir": file.is_dir(),
        "size": file.stat().st_size
    }

    files = os.scandir(args[0])
    return list(map(fileToJson, list(files)))


def delete_file(args: list) -> bool:
    path = args[0]
    
    if os.path.isfile(path):
        os.remove(path)
    else:
        os.rmdir(path)
    return True


available_cmds = {
	"ls_dir":      list_dir,
	"delete_file": delete_file,
	# "rename_file": renameFile,
}