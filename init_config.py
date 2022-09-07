#!/usr/bin/env python3

import tekore as tk

secret_config_file_name = 'config-secret.cfg'

conf = tk.config_from_environment(return_refresh=False)
token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
tk.config_to_file(secret_config_file_name, conf + (token.refresh_token,))
