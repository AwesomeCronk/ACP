from .installing import *
from .repositories import *
from .information import *


commands = {
    'install': command_install,
    'add-repo': command_add_repo,
    'update-repos': command_update_repos,
    'info': command_info,
    'docs': command_docs
}
