import styles from "../../css/index.module.css";
import Chat from "./MainSelectChat";
import {useState} from "react";
import axios from "axios";
import config from "../../config";
import {auth_headers} from "../../controllers/userController";
import NewInterlocutor from "./MainNewUser";

function LeftPanel({ chats, filter, chat_object, setChat }) {
    const [new_users, setNewUsers] = useState(null);
    let data;


    async function getChatMessages(chat_data) {
        if (chat_object.id === chat_data.id) return;

        axios.get(`${config.url}/message/chat/${chat_data.id}`, auth_headers()).then((response) => {
            setChat({id: Number(chat_data.id), interlocutor: chat_data.interlocutor,
                messages: Object.entries(response.data.items).map(([_, value]) => value), exist: true});
        })
    }


    if (chats === null) return;

    if (filter !== null) {
        data = Object.fromEntries(Object.entries(chats).filter(
            ([_, value]) => new RegExp(`(\\S*)${filter}(\\S*)`).test(value.interlocutor.username)));

        if (new_users === null || new_users.recent !== filter) {
            axios.get(`${config.url}/chat/to_create_with/${filter}`, auth_headers()).then(
                (response) => setNewUsers(
                    {recent: filter, content: Object.entries(response.data.items).map(([_, value]) => value)}));
        }
    } else { data = chats; if (new_users !== null) setNewUsers(null) }

    data = Object.entries(data);

    data.sort((a, b) => {
        let date1 = new Date(Date.parse(a[1].last_message.created_at));
        let date2 = new Date(Date.parse(b[1].last_message.created_at));

        if (date1 > date2)
            return -1;
        else if (date1 < date2)
            return 1;
        return 0;
    });

    return (
        <>
            <div className={styles.chatList}>
                { data.map(([key, value]) => (<div key={key} onClick={
                    () => getChatMessages({id: Number(key), ...value})} className={styles.chat}><Chat data={value}/></div>)) }
            </div>
            <div>
                { new_users === null ? null : new_users.content.map((data) => <NewInterlocutor key={data.id} data={data} setChat={setChat}/>) }
            </div>
        </>
    )
}

export default LeftPanel;