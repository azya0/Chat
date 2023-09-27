import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import styles from "../../css/index.module.css";
import {faArrowDown, faFrog, faPaperPlane} from "@fortawesome/free-solid-svg-icons";
import scrollHandler from "./scrollHandler";
import Message from "./MainMessage";
import {currentUser} from "../../controllers/userController";
import React from "react";

function MainChat({ chat, scroll, messageContent, send }) {
    return (
        <main>
            {  Object.keys(chat).length === 0 ? <FontAwesomeIcon className={styles.frogIcon} icon={faFrog} /> :
                <> { chat.exist ? (
                    <div id='messageContainer' className={styles.messageContainer} onScroll={scrollHandler}>
                        { chat.messages.map((data) => <Message key={data.id} message={data} style={
                            currentUser().id === data.author.id ? styles.messageOwn : styles.messageInterlocutor
                        }/>) }
                        <FontAwesomeIcon id='scroller' icon={faArrowDown} onClick={scroll} style={{'visibility': 'hidden'}}/>
                    </div>
                    ) : (
                        <div className={styles.welcome}>
                            <div>
                                <FontAwesomeIcon icon={faFrog} />

                                <h2>Write your first message for {chat.data.username}</h2>
                            </div>
                        </div>
                    ) }
                <footer>
                    <div className={styles.messageInput} contentEditable={true} ref={messageContent}/>

                    <FontAwesomeIcon onClick={send} icon={faPaperPlane}/>
                </footer>
            </> }
        </main>
    )
}

export default MainChat;