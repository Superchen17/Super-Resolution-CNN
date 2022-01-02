function CustomButton({Component, text, onClick}) {
  return (
    <div onClick={onClick}>
      <div className='
        flex w-fit border-2 p-2
        rounded-full bg-black text-white border-dotted border-white
        hover:bg-gray-400 cursor-pointer
      '>
        <Component className='h-8 my-auto'/>
        <p className="my-auto ml-1 mr-2 hidden md:flex">{text}</p>
      </div>
    </div>
  )
}

export default CustomButton
