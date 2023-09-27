import formatTime from "./formatTime";

function Message({ message, style }) {
    return (
        <div className={style}>
            { String(message.content).replaceAll('<br>', '\n') }
            <span> { formatTime(message['created_at']) } </span>
        </div>
    )
}

export default Message;
