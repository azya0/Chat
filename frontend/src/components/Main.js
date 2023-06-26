import React, {useEffect, useState} from 'react';
import {Navigate} from "react-router-dom";
import axios from "axios";

import {auth_headers, clearCurrentUser, currentUser} from "../controllers/UserController";
import styles from '../css/index.module.css';

function Chat({ data }) {
    function FormatDate(data) {
        const date = new Date(Date.parse(data));

        let year = new Intl.DateTimeFormat('en', { year: '2-digit' }).format(date);
        let month = new Intl.DateTimeFormat('en', { month: '2-digit' }).format(date);
        let day = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(date);

        return `${day}.${month}.${year}`;
    }

    function FormatTime(data) {
        const date = new Date(Date.parse(data));

        let hour = new Intl.DateTimeFormat('ru', {hour: 'numeric'}).format(date);
        let minute = new Intl.DateTimeFormat('en', {minute: '2-digit'}).format(date);

        return `${hour}:${minute}`;
    }

    return (
        <div className={styles.chat}>
            <div>
                <h4>{data["interlocutor"].username}</h4>
                <p>{FormatTime(data["last_message"]["created_at"])}</p>
            </div>
            <p>{data["last_message"].content}</p>
        </div>
    )
}

function Main() {
    const [chats, setChats] = useState([]);

    useEffect(() => {
        async function getChats() {
            try {
                const response = await axios.get('http://localhost:443/chat/all', auth_headers());

                setChats(response.data.items);
            }
            catch (error) {
                console.log(error);
            }
        }

        if (chats.length === 0) {
            getChats();
        }
    }, [chats.length]);

    const user = currentUser();

    return (user !== null) ? (
        <>
            <div className={styles.header}>
                <div className={styles.welcome}>
                    <h1>Welcome, {user.username}!</h1>
                    <button type='button' onClick={() => {clearCurrentUser(); window.location.href = '/auth';}}>LogOut</button>
                </div>
                {/*<div className={styles.find}>*/}
                {/*    <input/>*/}
                {/*    <button type="button">Find</button>*/}
                {/*</div>*/}
            </div>
            <div className={styles.chatList}>
                {chats.map((data, index) => <Chat key={index} data={data}/>)}
            </div>
        </>
    ) : (<Navigate to="/auth"/>);
}

export default Main;