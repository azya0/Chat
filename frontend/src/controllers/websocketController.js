import config from "../config";


class WebsocketController {
    constructor() {
        this.current = null;
    }

    exist = () => {
        return this.current !== null;
    }

    connect = () => {
        this.current = new WebSocket(`${config.ws_url}/connect`);
    }

    disconnect = () => {
        if (this.current !== null) {
            this.current.close()
            this.current = null;
        }
    }

    send = (user_id, message) => {
        if (this.current === null)
            return;

        this.current.send(`${user_id}:${message}`);
    }

    onmessage = (_function) => {
        if (this.current !== null)
            this.current.onmessage = _function;
    }
}

let connection = new WebsocketController();

export default connection;
