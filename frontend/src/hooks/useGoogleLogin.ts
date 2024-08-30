import { createEffect, createMemo } from "solid-js";
import {
    useGoogleOAuth,
    GoogleOAuthContextProps,
} from "../contexts/GoogleOAuthProvider";

import {
    TokenClientConfig,
    TokenResponse,
    CodeClientConfig,
    CodeResponse,
    OverridableTokenClientConfig,
    NonOAuthError,
} from "../@types/index";

interface ImplicitFlowOptions
    extends Omit<TokenClientConfig, "client_id" | "scope" | "callback"> {
    onSuccess?: (
        tokenResponse: Omit<
            TokenResponse,
            "error" | "error_description" | "error_uri"
        >,
    ) => void;
    onError?: (
        errorResponse: Pick<
            TokenResponse,
            "error" | "error_description" | "error_uri"
        >,
    ) => void;
    onNonOAuthError?: (nonOAuthError: NonOAuthError) => void;
    scope?: TokenClientConfig["scope"];
    overrideScope?: boolean;
}

interface AuthCodeFlowOptions
    extends Omit<CodeClientConfig, "client_id" | "scope" | "callback"> {
    onSuccess?: (
        codeResponse: Omit<
            CodeResponse,
            "error" | "error_description" | "error_uri"
        >,
    ) => void;
    onError?: (
        errorResponse: Pick<
            CodeResponse,
            "error" | "error_description" | "error_uri"
        >,
    ) => void;
    onNonOAuthError?: (nonOAuthError: NonOAuthError) => void;
    scope?: CodeResponse["scope"];
    overrideScope?: boolean;
}

export type UseGoogleLoginOptionsImplicitFlow = {
    flow?: "implicit";
} & ImplicitFlowOptions;

export type UseGoogleLoginOptionsAuthCodeFlow = {
    flow?: "auth-code";
} & AuthCodeFlowOptions;

export type UseGoogleLoginOptions =
    | UseGoogleLoginOptionsImplicitFlow
    | UseGoogleLoginOptionsAuthCodeFlow;

export default function useGoogleLogin({
    flow = "implicit",
    scope = "",
    onSuccess,
    onError,
    onNonOAuthError,
    overrideScope,
    state,
    ...props
}: UseGoogleLoginOptions) {
    const context = useGoogleOAuth();
    const { clientId, scriptLoadedSuccessfully } =
        context as GoogleOAuthContextProps;
    let clientRef: any;

    const onSuccessMemo = createMemo(() => onSuccess);
    const onErrorMemo = createMemo(() => onError);
    const onNonOAuthErrorMemo = createMemo(() => onNonOAuthError);

    createEffect(() => {
        if (!scriptLoadedSuccessfully()) return;
        const clientMethod =
            flow === "implicit" ? "initTokenClient" : "initCodeClient";
        const client = window?.google?.accounts?.oauth2[clientMethod]({
            client_id: clientId,
            scope: overrideScope ? scope : `openid profile email ${scope}`,
            callback: (response: TokenResponse | CodeResponse) => {
                if (response.error) return onErrorMemo()?.(response);
                onSuccessMemo()?.(response as any);
            },
            error_callback: (nonOAuthError: NonOAuthError) => {
                onNonOAuthErrorMemo()?.(nonOAuthError);
            },
            state,
            ...props,
        });
        clientRef = client;
    }, [clientId, scriptLoadedSuccessfully, flow, scope, state]);

    // NOTE: Original causes TS error in App.tsx component
    // TODO: Address TS Error regarding event handler
    // const loginImplicitFlow = (overrideConfig?: OverridableTokenClientConfig) =>
    // clientRef?.requestAccessToken(overrideConfig);

    const loginImplicitFlow = () => clientRef?.requestAccessToken();
    const loginAuthCodeFlow = () => clientRef?.requestCode();

    return flow === "implicit" ? loginImplicitFlow : loginAuthCodeFlow;
}
