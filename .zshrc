export PATH="$PATH:$HOME/FlutterDev/flutter/bin"


## [Completion] 
## Completion scripts setup. Remove the following line to uninstall
[[ -f /Users/alvin/.dart-cli-completion/zsh-config.zsh ]] && . /Users/alvin/.dart-cli-completion/zsh-config.zsh || true
## [/Completion]

alias python=/usr/bin/python3

export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/alvin/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/alvin/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/alvin/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/alvin/google-cloud-sdk/completion.zsh.inc'; fi

# Created by `pipx` on 2024-10-13 09:50:01
export PATH="$PATH:/Users/alvin/.local/bin"

# Added by Windsurf
export PATH="/Users/alvin/.codeium/windsurf/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
