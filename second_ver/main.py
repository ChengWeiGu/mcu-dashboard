from App import WaveFormApp
import sys, subprocess
sys.setrecursionlimit(1000000)

######打包時加入版號########
try:
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = sys._MEIPASS
        build_verfile = open(os.path.join(bundle_dir, 'build_revision'), 'r')
        version = build_verfile.readline()
        version = version.split("\n")[0]
        build_verfile.close()
    else:
        # we are running in a normal Python environment
        version = subprocess.check_output("svnversion").decode('utf-8').split(":")[-1].split("\r")[0]

except (FileNotFoundError, AttributeError) as e:
    print("Revision not found")


if __name__ == "__main__":
    
    waveformapp = WaveFormApp()
    print('run the server......')
    waveformapp.app.run_server(port = waveformapp.web_port, host = waveformapp.web_host)