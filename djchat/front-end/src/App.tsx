import Home from "./pages/Home";
import { createBrowserRouter, createRoutesFromElements, Route, RouterProvider } from "react-router-dom";


const router= createBrowserRouter(
  createRoutesFromElements( 
    <Route>
    <Route path="/" element={<Home />} />
    </Route>
  )
);


const App = () => {
  return <RouterProvider router={router} />;
};
export default App;