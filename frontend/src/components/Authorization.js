import {setCurrentUser, currentUser} from "../controllers/UserController";
import {Navigate} from "react-router-dom";

import styles from '../css/form.module.css';

function Authorization() {
    async function Submit(data) {
        data.preventDefault();

        await setCurrentUser(data.target[0].value, data.target[1].value);

        window.location.href = '/'; // TOFIX
    }

    return (currentUser() === null) ? (
        <form className={styles.form} onSubmit={Submit}>
            <h3>email</h3>
            <input type='email'/>
            <h3>password</h3>
            <input type='password'/>
            <div>
                <button>Submit</button>
                <button type="button" onClick={() => window.location.href = '/reg'}>Have no account</button>
            </div>
        </form>
    ) : (
        <Navigate to="/"/>
    );
}

export default Authorization;
