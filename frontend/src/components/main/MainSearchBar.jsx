import styles from "../../css/index.module.css";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faMagnifyingGlass} from "@fortawesome/free-solid-svg-icons";
import React from "react";

function SearchBar({ filter_function }) {
    return (
        <div id='search-bar' className={styles.searchBar}>
            <input id='search-input' onClick={() => {
                document.getElementById('search-bar').classList.add(styles.searchBarSelected);
            }} onBlur={() => {
                document.getElementById('search-bar').classList.remove(styles.searchBarSelected);
            }} onChange={(event) => {
                filter_function(event.target.value);
            }} type='search' />
            <FontAwesomeIcon icon={faMagnifyingGlass} style={
                { height: "1rem", marginLeft: ".5rem", }
            }/>
        </div>
    )
}

export default SearchBar;