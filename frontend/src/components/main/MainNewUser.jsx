import styles from '../../css/index.module.css';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faPlus} from "@fortawesome/free-solid-svg-icons";


function NewInterlocutor({ data, setChat }) {
    return (
        <div className={styles.chatNew} onClick={() => setChat({id: data.id, data: data, exist: false})}>
            <h4>{ data.username }</h4>
            <FontAwesomeIcon icon={faPlus} />
        </div>
    );
}

export default NewInterlocutor;