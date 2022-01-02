import '../styles/globals.css'
import Header from '../components/header'

function MyApp({ Component, pageProps }) {
  return (
    <div className="flex flex-col flex-none w-screen h-screen">
      <div className="
        flex flex-col flex-none
        w-screen h-20 justify-center text-center 
        bg-black text-white
      ">
        <Header />
      </div>
      <div className="flex flex-col w-screen h-full justify-center overflow-auto">
        <Component {...pageProps} />
      </div>
    </div>
  )
}

export default MyApp
