import React, {useCallback, useEffect, useRef, useState} from 'react';
import {Navigate} from "react-router-dom";
import axios from "axios";

import {auth_headers, clearCurrentUser, currentUser, currentUserExist} from "../../controllers/userController";
import styles from '../../css/index.module.css';
import config from "../../config";
import connection from "../../controllers/websocketController";
import LeftPanel from "./MainLeftPanel";
import SearchBar from "./MainSearchBar";
import MainChat from "./MainChat";

function Main() {
    const user = currentUser();

    const messageContent = useRef(null);
    const [chat_list, setChats] = useState(null);
    const [filter, setFilter] = useState(null);
    const [chat, setChat] = useState({});

    const addMessage = useCallback((message) => {
        setChat({...chat, messages: [message, ...chat.messages]});
    }, [chat]);

    useEffect(() => {
        axios.get(`${config.url}/chat/all`, auth_headers()).then((response) => {
            const dict = {};

            Object.entries(response.data.items).map(([_, value]) => value).forEach(({id, ...rest}) => dict[id] = rest);

            setChats(dict);
        }).catch((error) => {
            if (error.response.request.status === 401) {
                clearCurrentUser();
                window.location.href = '/auth'
            }
        });

        connection.connect();
    }, []);

    function scrollBottom() {
        document.getElementById('messageContainer').firstElementChild.scrollIntoView({behavior: 'smooth'});
    }

    useEffect(() => {
        if (Object.keys(chat).length === 0 || !chat.exist) return;

        if (chat.messages[0].author.id === currentUser().id) {
            scrollBottom();
        }
    }, [chat, chat.messages]);

    useEffect(() => {
        connection.onmessage((event) => {
            const message_data = JSON.parse(event.data);

            console.log([chat, currentUser(), message_data]);

            let {chat_id, ...content} = message_data;

            if (chat_id === chat.id) addMessage(content);

            if (chat_id in chat_list) {
                chat_list[chat_id].last_message = content;
                setChats(chat_list);
            }
        });
    }, [addMessage, chat, chat_list]);

    function sendMessage() {
        let message = messageContent.current.innerHTML.replaceAll('&nbsp;', '');

        message = message.replaceAll('<br>', '\n').trim();

        messageContent.current.innerHTML = '';

        if (message === '') return;

        if (chat.exist) {
            axios.post(`${config.url}/message/chat/${chat.id}`, {},
                {...auth_headers(), params: { message: message }}).then(
                (response) => {
                    addMessage({author: currentUser(), ...response.data});

                    chat_list[chat.id].last_message = response.data;
                    setChats(chat_list);
                }
            );
            return;
        }

        axios.post(`${config.url}/chat/user/id/${chat.id}`, {},
            {...auth_headers(), params: {message: message}}).then(
                (response) => {
                    let current_chat = response.data;

                    let chat_dict = {};
                    chat_dict[current_chat.id] = current_chat;

                    setChats({...chat_dict, ...chat_list});

                    document.getElementById('search-input').value = '';

                    setFilter(null);

                    setChat({id: Number(current_chat.id), interlocutor: current_chat.interlocutor,
                        messages: [current_chat.last_message], exist: true});
        });
    }

    function filter_chats(filter_string) {
        if (filter_string === '') { setFilter(null); return; }

        setFilter(filter_string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    }

    return (currentUserExist()) ? (
        <div className={styles.base}>
            <nav>
                <header>
                    <button onClick={() => { clearCurrentUser() } }><h3>Welcome, {user.username}</h3></button>
                </header>
                <SearchBar filter_function={filter_chats}/>
                <LeftPanel filter={filter} chats={chat_list} chat_object={chat} setChat={setChat}/>
            </nav>
            <MainChat chat={chat} scroll={scrollBottom} messageContent={messageContent} send={sendMessage}/>
        </div>
    ) : (<Navigate to="/auth"/>);
}


export default Main;
