import { createSignal, Accessor, onCleanup } from "solid-js";

export interface UseLoadGsiScriptOptions {
    nonce?: string;
    onScriptLoadSuccess?: () => void;
    onScriptLoadError?: () => void;
}

export default function useLoadGsiScript(
    options: UseLoadGsiScriptOptions = {},
): Accessor<boolean> {
    const { nonce, onScriptLoadSuccess, onScriptLoadError } = options;

    const [scriptLoadedSuccessfully, setScriptLoadedSuccessfully] =
        createSignal(false);

    const scriptTag = document.createElement("script");
    scriptTag.src = "https://accounts.google.com/gsi/client";
    scriptTag.async = true;
    scriptTag.defer = true;
    if (nonce) scriptTag.nonce = nonce;

    scriptTag.onload = () => {
        setScriptLoadedSuccessfully(true);
        onScriptLoadSuccess?.();
    };

    scriptTag.onerror = () => {
        setScriptLoadedSuccessfully(false);
        onScriptLoadError?.();
    };

    document.body.appendChild(scriptTag);
    onCleanup(() => {
        document.body.removeChild(scriptTag);
    });

    return scriptLoadedSuccessfully;
}
