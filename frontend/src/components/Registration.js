import axios from "axios";
import {setCurrentUser, currentUser} from "../controllers/UserController";
import {Navigate} from "react-router-dom";

import styles from '../css/form.module.css';

function Registration() {
    async function Submit(data) {
        data.preventDefault();

        if (data.target[2].value.toLowerCase() !== data.target[3].value.toLowerCase()) {
            alert('Пароли не совпадают! Пошел нахуй!');
            return;
        }

        let response_data = {
            'username': data.target[0].value,
            'email': data.target[1].value,
            'password': data.target[2].value,
        }

        try {
            const response = await axios.post('http://localhost:443/auth/register', response_data);

            await setCurrentUser(response.data['email'], data.target[2].value);

            window.location.href = '/';
        }
        catch (error) {
            console.log(error);
        }
    }

    return (currentUser() === null) ? (
        <form className={styles.form} onSubmit={Submit}>
            <h3>username</h3>
            <input type='login'/>
            <h3>email</h3>
            <input type='email'/>
            <h3>password</h3>
            <input type='password'/>
            <h3>repeat password</h3>
            <input type='password'/>
            <div>
                <button>Submit</button>
                <button type='button' onClick={() => window.location.href = '/auth'}>Login</button>
            </div>
        </form>
    ) : (
        <Navigate to='/'/>
    );
}

export default Registration;
