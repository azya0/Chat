import styles from "../../css/index.module.css";
import React from "react";
import formatTime from "./formatTime";

function Chat({ data }) {
    if (data === undefined) return;

    return (
        <>
            <div>
                <h4>{data["interlocutor"]["username"]}</h4>
                <p className={styles.time}>{formatTime(data["last_message"]["created_at"])}</p>
            </div>
            <p>{data["last_message"]["content"]}</p>
        </>
    );
}

export default Chat;
