import Cookies from "js-cookie";
import axios from "axios";

function auth_headers() {
    return (Cookies.get('access_token') !== null) ? {
        headers: {Authorization: `${Cookies.get('token_type')} ${Cookies.get('access_token')}`},
    } : {};
}

async function setCurrentUser(email, password) {
    async function GetToken(email, password) {
        const params = new URLSearchParams({ 'username': email, 'password': password });

        try {
            let response = await axios.post('http://localhost:443/auth/jwt/login', params);
            return response.data;
        }
        catch (error) {
            console.log(error);
        }
    }

    try {
        const data = await GetToken(email, password);

        for (const [key, value] of Object.entries(data)) {
            Cookies.set(key, value);
        }

        const response = await axios.get('http://localhost:443/users/me', auth_headers());

        localStorage.setItem('current_user', JSON.stringify(response.data));
    }
    catch (error) {
        console.log(error);
    }
}

function currentUser() {
    if (Cookies.get('access_token') == null) {
        localStorage.setItem('current_user', null);
        return null;
    }

    const data = localStorage.getItem('current_user');

    if (data !== null)
        return JSON.parse(data);

    return null;
}

function clearCurrentUser() {
    localStorage.setItem('current_user', null);

    Cookies.remove('access_token');
    Cookies.remove('token_type');
}

export {auth_headers, setCurrentUser, currentUser, clearCurrentUser};
