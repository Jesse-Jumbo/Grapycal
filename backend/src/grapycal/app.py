import os
import shutil
import signal
import sys
from typing import Any, Callable, Dict
import subprocess
from .utils.file import get_direct_sub_folders
import termcolor
import time
from importlib.metadata import version as get_version

class GrapycalApp:
    """
    The backend server

    :param usersettings.Settings config: the configuration for server
    """
    def __init__(self, config) -> None:
        self._config = config
        if not config['path'].endswith('.grapycal'):
            config['path'] += '.grapycal'

    def run(self) -> None:
        """
        Server main loop
        """
        version = get_version('grapycal')
        print(
            termcolor.colored(r'''
               ______                                  __
              / ____/________ _____  __  ___________ _/ /
             / / __/ ___/ __ `/ __ \/ / / / ___/ __ `/ / 
            / /_/ / /  / /_/ / /_/ / /_/ / /__/ /_/ / /  
            \____/_/   \__,_/ .___/\__, /\___/\__,_/_/   
                           /_/    /____/
                                           ''','red') + termcolor.colored('v'+version, 'white'))
        print()

        #TODO: Support multiple workspaces
        #TODO: Websocket multiplexing

        workspace = None
        http_server = None
        # Here simply start one workspace in background
        while True:
            break_flag = False
            try:
            
                # Start webpage server
                if not self._config['no_serve_webpage']:
                    webpage_path = os.path.join(os.path.dirname(__file__),'webpage')
                    print(f'Strating webpage server at localhost:{self._config["http_port"]} from {webpage_path}...')
                    http_server = subprocess.Popen([sys.executable,'-m', 'http.server',str(self._config["http_port"])],
                                     start_new_session=True,cwd=webpage_path,
                                     stdout=subprocess.DEVNULL
                                     )

                while True: # Restart workspace when it exits. Convenient for development

                    # Start workspace
                    print(f'Starting workspace {self._config["path"]} at {self._config["host"]}:{self._config["port"]}...')
                    workspace = subprocess.Popen([sys.executable,'-m', 'grapycal.core.workspace',
                        '--port', str(self._config['port']),
                        '--host', self._config['host'],
                        '--path', self._config['path']],start_new_session=True)
                    
                    while True:
                        time.sleep(1)
                        if workspace.poll() is not None:
                            print('Workspace exited with code',workspace.poll())
                            break

                    if not self._config['restart']:
                        break

            except KeyboardInterrupt:
                print('Shutting down Grapycal server will force kill all workspaces. Press Ctrl+C again to confirm.')
                try:
                    time.sleep(3)
                except KeyboardInterrupt:
                    break_flag = True
                else:
                    print('Resumed')
            if break_flag:
                break

        print('Stopping workspaces...')
        if workspace:
            workspace.send_signal(signal.SIGTERM)
            workspace.wait()
        if http_server:
            http_server.send_signal(signal.SIGTERM)
            http_server.wait()
        print('Grapycal server terminated')
        return
    