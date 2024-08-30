import {
    createContext,
    useContext,
    createMemo,
    Accessor,
    ParentComponent,
} from "solid-js";
import useLoadGsiScript, {
    UseLoadGsiScriptOptions,
} from "../hooks/useLoadGsiScript";

export interface GoogleOAuthContextProps {
    clientId: string;
    scriptLoadedSuccessfully: Accessor<boolean>;
}

export const GoogleOAuthContext = createContext<GoogleOAuthContextProps>(null!);

interface GoogleOAuthProviderProps extends UseLoadGsiScriptOptions {
    clientId: string;
}

export const GoogleOAuthProvider: ParentComponent<
    GoogleOAuthProviderProps
> = props => {
    const scriptLoadedSuccessfully = useLoadGsiScript({
        nonce: props.nonce,
        onScriptLoadSuccess: props.onScriptLoadSuccess,
        onScriptLoadError: props.onScriptLoadError,
    });

    const contextValue = createMemo(() => ({
        clientId: props.clientId,
        scriptLoadedSuccessfully,
    }));

    return (
        <GoogleOAuthContext.Provider value={contextValue()}>
            {props.children}
        </GoogleOAuthContext.Provider>
    );
};

export function useGoogleOAuth() {
    const context = useContext(GoogleOAuthContext);
    if (!context) {
        throw new Error(
            "Google OAuth components must be used within GoogleOAuthProvider",
        );
    }
    return context;
}
