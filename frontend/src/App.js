import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Registration from "./components/Registration";
import Authorization from "./components/Authorization";
import Main from "./components/main/Main";

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
