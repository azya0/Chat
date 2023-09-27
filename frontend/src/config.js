class Config {
    constructor() {
        this.protocol = process.env.REACT_APP_SERVER_PROTOCOL;
        this.host = process.env.REACT_APP_SERVER_HOST;
        this.port = process.env.REACT_APP_SERVER_PORT;

        this.url = `${this.protocol}://${this.host}:${this.port}`
        this.ws_url = `ws://${this.host}:${this.port}/message`
    }
}

const config = new Config();

export default config;
