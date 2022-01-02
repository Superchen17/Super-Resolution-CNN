import { PhotographIcon } from '@heroicons/react/solid';

function Viewport({imgSrc, title}) {
  return (
    <div className="flex flex-col w-1/2 h-full p-2 text-center">
      <div className="flex justify-center p-1 w-full">
        <h1 className="text-lg font-bold">{title}</h1>
      </div>
      <div className="
        flex
        flex-col 
        h-full w-full justify-center p-1
        overflow-auto
      ">
        {
          !(imgSrc) 
          ?(
            <div className="h-full w-full flex flex-col justify-center">
              <PhotographIcon className='h-12 md:h-24'/>
            </div>
          )
          :(
            <img className="h-screen w-screen object-cover" src={imgSrc}/>
          )
        }
      </div>
    </div>
  )
}

export default Viewport
