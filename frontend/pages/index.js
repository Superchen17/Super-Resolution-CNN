import { UploadIcon, ServerIcon, CheckIcon, XCircleIcon } from '@heroicons/react/solid'
import {useRef, useState, useEffect} from 'react'
import CustomButton from '../components/botton'
import Viewport from "../components/view-port"
import { socket } from '../components/socket'
import {Dialog} from '@material-ui/core'

export default function Home() {

  /**
   * constants
   */
  const ACCEPTED_FILE_FORMATS = ['jpg', 'jpeg', 'png'];

  /**
   * states
   */
  /** internal state */
  /** 0: no file uploaded to local */
  /** 1: file at local, ready to be uploaded or discarded */
  /** 2: file at server, ready to be superresolved or discarded */
  const [localState, setLocalState] = useState(0);
  /** local image file ready to be uploaded to server */
  const [file, setFile] = useState(null);
  /**  full path of image file on server */
  const [fileName, setFileName] = useState(null);
  /** image base64 str before superresolution */
  const [imgBefore, setImageBefore] = useState(null);
  /** image base64 str after superresolution */
  const [imgAfter, setImageAfter] = useState(null);
  /** list of image names in the gallary */
  const [gallary, setGallary] = useState(null);
  /** dialog open/close */
  const [dialogOpen, setDialogOpen] = useState(false);
  /** psnr of the superresolved image */
  const [psnr, setPsnr] = useState(null);

  /**
   * references
   */
  const fileSelectorRef = useRef(null);

  useEffect(() => {
    socket.on('r_list_gallary', (r) => {
      setGallary(r.data.dataset);
      setDialogOpen(true);
      console.log(r.data.dataset);
    });
  }, [])

  useEffect(() => {
    socket.on('r_get_image', (r) => {
      const imgBeforeSrc = _get_image_url_from_bytes(r.data.image)
      setImageBefore(imgBeforeSrc);
      setImageAfter(null);
      setPsnr(null);
      setFileName(r.data.path);
      setDialogOpen(false);
      setLocalState(2);
    });
  }, []);

  useEffect(() => {
    socket.on('r_run_superres', (r) => {
      const imgAfterSrc = _get_image_url_from_bytes(r.data.image)
      setImageAfter(imgAfterSrc);
      setPsnr(r.data.metrics.psnr);
      setLocalState(0);
    });
  }, []);

  const _get_image_url_from_bytes = (bytes) => {
    var arrayBufferView = new Uint8Array(bytes);
    var blob = new Blob( [ arrayBufferView ], { type: "image/png" } );
    var imgUrl = URL.createObjectURL(blob);
    return imgUrl;
  }

  const fileSelectorHandler = event => {
    event.preventDefault();
    const fileName = event.target.files[0].name;

    const indexPeriod = fileName.lastIndexOf('.');
    const suffix = fileName.slice(indexPeriod+1);
    console.log(suffix);

    if(!ACCEPTED_FILE_FORMATS.includes(suffix)){
      alert('invalid file format, must be .jpg, .jpeg or .png');
      return;
    }

    setFile(event.target.files[0]);
    setFileName(event.target.files[0].name)
    setLocalState(1);
  }

  const fileUploadHandler = () => {
    const reader = new FileReader();
    reader.onload= () => {
        const data = reader.result;
        const binaryArray = new Int8Array(data);

        const inJson = {
          data: {
            image: binaryArray
          }
        }
        socket.emit('upload_image', inJson);
    }
    reader.readAsArrayBuffer(file);
  }

  const gallarySelectorHandler = () => {
    socket.emit('list_gallary');
  }

  const gallaryFileHandler = event => {
    console.log(event.target.id);
    const inJson = {
      data: {
        dir: 'gallary',
        file_name: event.target.id
      }
    };
    setFileName(event.target.id)
    socket.emit('get_image', inJson);
  }

  const algorithmExecuteHandler = () => {
    const inJson = {
      data: {
        path: fileName
      }
    };
    console.log(inJson);
    socket.emit('run_superres', inJson);
  }

  const resetStates = () => {
    setLocalState(0);
    setFile(null);
    setImageBefore(null);
    setImageAfter(null);
    setPsnr(null);
  }

  return (
    <>
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        {
          (gallary) && (
            <div className='flex flex-col justify-top w-64 h-48 p-3 space-y-1'>
              {gallary.map(entry=>
                <div 
                  className='
                    ml-3 font-bold italic 
                    hover:text-blue-400 hover:cursor-pointer hover:bg-gray-200
                  '
                  onClick={gallaryFileHandler}
                  id={entry}
                >
                  {entry}
                </div>
              )}
            </div>
          )
        }
      </Dialog>
      <div className="flex flex-col h-full w-full justify-top">
        <div className="flex flex-row h-5/6 w-full">
          <Viewport imgSrc={imgBefore} title={'Original'}/>
          <Viewport imgSrc={imgAfter} title={'Super Resolved'}/>
        </div>
        <div className="flex flex-row p-1 grow bg-gray-200">
          <div className="flex flex-row w-1/2 justify-center space-x-2 my-auto md:space-x-10">
            <input className='hidden' type={'file'} onChange={fileSelectorHandler} ref={fileSelectorRef}/>
            {
              (()=>{
                if(localState == 0){
                  return(
                    <>
                      <CustomButton 
                        Component={UploadIcon} 
                        text={'Upload New'} 
                        onClick={() => fileSelectorRef.current.click()}
                      />
                      <CustomButton 
                        Component={ServerIcon} 
                        text={'Browse Gallary'}
                        onClick={() => gallarySelectorHandler()}
                      />
                    </>
                  )
                }
                else if(localState == 1){
                  return (
                    <>
                      <p className='my-auto italic'>{file.name}</p>
                      <CustomButton 
                        Component={CheckIcon} 
                        text={'Confirm'} 
                        onClick={fileUploadHandler}
                      />
                      <CustomButton 
                        Component={XCircleIcon} 
                        text={'Remove'} 
                        onClick={resetStates}
                      />
                    </>
                  )
                }
                else if(localState == 2){
                  return (
                    <>
                      <CustomButton 
                        Component={CheckIcon} 
                        text={'Apply Super-Resolution'} 
                        onClick={algorithmExecuteHandler}
                      />
                      <CustomButton 
                        Component={XCircleIcon} 
                        text={'Cancel'} 
                        onClick={resetStates}
                      />
                    </>
                  )
                }
              })()
            }
          </div>
          <div className='flex flex-col justify-top w-1/2'>
            <p className='mx-auto font-medium'>Metrics</p>
            {
              (psnr) && <p className='mx-auto italic'>PSNR: {psnr}</p>
            }
          </div>
        </div>
      </div>
    </>
  )
}
