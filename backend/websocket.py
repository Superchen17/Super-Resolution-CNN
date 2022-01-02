import os
from flask import Flask, request
from flask_socketio import SocketIO, emit
from concurrent.futures import ThreadPoolExecutor

import worker

# map sid to a worker
# spawn a worker upon a new connection
# remove the worker when disconnected
workerPool = {}

app =Flask(__name__)
sio = SocketIO(app, cors_allowed_origins='*')

def _get_allocated_worker() -> worker.Worker:
    '''return the client's allocated worker by sid
    
    '''
    print(request.sid)
    return workerPool[request.sid]

@sio.on('connect')
def handle_connect():
    '''upon connection, allocate a worker to the client
    
    '''
    sid = request.sid
    if sid not in workerPool.keys():
        workerPool[sid] = worker.Worker()

    print('connected', sid)

@sio.on('list_gallary')
def handle_list_gallary():
    '''list available images in gallary
    
    '''
    w = _get_allocated_worker()
    dataset = w.list_gallary()
    r = {}
    r['data'] = {}
    r['data']['dataset'] = dataset
    emit('r_list_gallary', r)

@sio.on('get_image')
def handle_get_image(inJson):
    '''send a requested image to the client
    
    '''
    dir = inJson['data']['dir']
    imgFileName = inJson['data']['file_name']

    w = _get_allocated_worker()
    imagePath, image = w.get_image(dir, imgFileName)

    r = {}
    r['data'] = {}
    r['data']['image'] = image
    r['data']['path'] = imagePath
    emit('r_get_image', r)

@sio.on('run_superres')
def handle_run_superres(inJson):
    '''execute the superresolution algorithm
    
    '''
    imagePath = inJson['data']['path']

    w = _get_allocated_worker()
    with ThreadPoolExecutor() as executor:
        t = executor.submit(w.superresolve_color, imagePath)
    outImage, psnr = t.result()

    r = {}
    r['data'] = {}
    r['data']['image'] = outImage
    r['data']['metrics'] = {}
    r['data']['metrics']['psnr'] = psnr
    emit('r_run_superres', r)

@sio.on('upload_image')
def handle_upload_image(inJson):
    '''receive uploaded image from the client
    
    '''
    imageByteArr = inJson['data']['image']
    w = _get_allocated_worker()
    imagePath, image = w.save_uploaded_image(imageByteArr)

    r = {}
    r['data'] = {}
    r['data']['path'] = imagePath
    r['data']['image'] = image
    emit('r_get_image', r)

@sio.on('disconnect')
def handle_disconnect():
    '''upon client disconnection,
    remove all generated file by this client,
    and remove its allocated worker 
    
    '''
    w = _get_allocated_worker()
    
    for filePath in w.get_generated_files():
        os.remove(path=filePath)

    del workerPool[request.sid]
    print('Client disconnected')

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=8888, debug=True)
