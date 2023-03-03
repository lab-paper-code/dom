export PATH="/usr/local/cuda/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
export PATH="/usr/local/ffmpeg:$PATH"
echo "PATH UPDATED"
python3 /DOM/server/app.py -p ${1}
