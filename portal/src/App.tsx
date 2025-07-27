
import './App.css'
import { FrappeProvider } from 'frappe-react-sdk'
import { ToastContainer } from 'react-toastify';
import { RouterProvider } from 'react-router-dom'
import { router } from './routers/router'
function App() {
  return (
	<div className="App">
	  <FrappeProvider siteName={"http://localhost:8000/"} enableSocket={false}>
	  <ToastContainer />
	  <RouterProvider router={router} />
	  </FrappeProvider>
	</div>
  )
}

export default App
