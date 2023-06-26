import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Registration from "./components/Registration";
import Authorization from "./components/Authorization";
import Main from "./components/Main";

function App() {
  return (
      <Router>
      <Routes>
        <Route path='/' element={<Main/>}/>
        <Route path='/reg' element={<Registration/>}/>
        <Route path='/auth' element={<Authorization/>}/>
      </Routes>
      </Router>
  );
}

export default App;
