import type { Component } from "solid-js";

import styles from "./App.module.css";

const App: Component = () => {
    return (
        <div class={styles.App}>
            <h1>Pikoshi</h1>
            <a href='/login'>Login</a>
        </div>
    );
};

export default App;
