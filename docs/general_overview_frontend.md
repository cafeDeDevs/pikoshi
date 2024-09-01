# General Overview - Frontend

## Introduction

Pikoshi's frontend codebase follows a modern implementation of the
[Model View Controller](https://en.wikipedia.org/w/index.php?title=Model%E2%80%93view%E2%80%93controller)(MVP)
Structure. Within the frontend, this generally is reflected in a folder
structure that many modern developers will be familiar with. Such familiar
directories as `components`, `contexts`, `hooks`, `views`, `utils`, `schemas`,
and `utils` are mainstays of the Pikoshi frontend.

Pikoshi utilizes the modern frontend framework
[SolidJS](https://www.solidjs.com/), which at the time of this writing
(09/01/2024), is less familiar to developers by comparison to other more popular
frameworks like [ReactJS](https://react.dev/), [VueJS](https://vuejs.org/), and
[SvelteJS](https://svelte.dev/). Thusly, there is some introduction necessary to
the basics of SolidJS in the context of it's use with Pikoshi so that new
developers can become familiar with it's conventions. Those who are familiar
with ReactJS, however, will find themselves quite at home within a SolidJS
codebase, as they both use JSX style syntax, and have many similar conventions
when dealing with Reactivity.

This document, however, will not aim to solely focus on the SolidJS conventions,
for which one should take a a look at
[SolidJS's documentation](https://docs.solidjs.com/). Instead, I will attempt to
walk you through navigating Pikoshi's frontend codebase, and ultimately gain a
better understanding of how everything pieces together.

### The index.tsx File

Pikoshi's frontend uses [Bun](https://bun.sh/) as it's package and project
manager, as well as [Vite](https://vitejs.dev/) as it's development server. One
can find the root of the initial SolidJS renderer in the `src/index.tsx` file:

```ts
/* @refresh reload */
import { render } from "solid-js/web";
import { Router } from "@solidjs/router";
import routes from "./router/index.tsx";

import "./index.css";

const root = document.getElementById("root");

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?",
  );
}

render(() => <Router>{routes}</Router>, root!);
```

One will not see much different from the setup of a classic ReactJS or VueJS
project instantiated using Vite. You'll notice that we use the SolidJS Router as
a Client Side Page Router. We also import SolidJS Router as a
[Config-Based Router](https://docs.solidjs.com/solid-router/getting-started/config).
Let's take a brief look at that configuration now:

### SolidJS Config-Based Router

Located within the `src/router/index.tsx` file, you'll find a layout of all our
Routes, each of which (except for `App.tsx`) come from the `views` directory:

```tsx
import Gallery from "../views/Gallery";
import Login from "../views/Login";
import Onboarding from "../views/Onboarding";
import Signup from "../views/Signup";

const routes = [
  {
    path: "/",
    component: App,
  },
  {
    path: "/login",
    component: Login,
  },
  {
    path: "/signup",
    component: Signup,
  },
  {
    path: "/onboarding",
    component: Onboarding,
  },
  {
    path: "/gallery",
    component: Gallery,
  },
];

export default routes;
```

If you haven't seen a Config-Based Router before, know that it is relatively
straight forward. Instead of the more commonly used approach of
[Component Routing](https://docs.solidjs.com/solid-router/getting-started/component),
Pikoshi utilizes this style of configuring the Page Router, and simply tells the
SolidJS Router to navigate to the assigned component whenever the user navigates
to the indicated/configured Path.

Let's start at the root path, "/".

### The App.tsx Component

There isn't much to see here, as it is simply the splash page at the moment:

```tsx
import type { Component } from "solid-js";

import styles from "./App.module.css";

const App: Component = () => {
  return (
    <div class={styles.App}>
      <h1>Pikoshi</h1>
      <a href="/login">Login</a>
    </div>
  );
};

export default App;
```

However, immediately we can see a difference between ReactJS and SolidJS.
SolidJS attempts to keep it's JSX closer to raw HTML as possible, and thusly
traditional HTML
[anchor tags](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a) work
with the Solid JS Router.

Let's navigate to the Login page then.

### The Login.tsx View

```tsx
import type { Component } from "solid-js";
import { GoogleOAuthProvider } from "../contexts/GoogleOAuthProvider";
import EmailLogin from "../components/EmailLogin";
import GoogleLoginBtn from "../components/GoogleLoginBtn.tsx";

const googleClientId = import.meta.env.VITE_GOOGLE_OAUTH2_CLIENT_ID;
const googleClientNonce = import.meta.env.VITE_GOOGLE_OAUTH2_NONCE;

import styles from "../css/AuthCard.module.css";

const Login: Component = () => {
  return (
    <div class={styles.AuthCard}>
      <h1>Login</h1>
      <EmailLogin />
      <p>Or Continue with:</p>
      <GoogleOAuthProvider
        clientId={googleClientId}
        nonce={googleClientNonce}
      >
        <GoogleLoginBtn />
      </GoogleOAuthProvider>
      <br />
      <br />
      <a href="/signup">Create an account</a>
    </div>
  );
};

export default Login;
```

This looks very similar to a React Component, doesn't it? Well... there is that
whole `styles.AuthCard` thing going on... and yeah, we see another anchor tag
leading us to a SolidJS Router route... but other than that, it's very similar.

We won't get into the nitty gritty of how SolidJS parses css files, sufficient
to say it encourages it's own conventions involving `module.css` files. it looks
like we can login here, but we haven't signed up yet, so let's click on the
`/signup` link...

### The Signup.tsx View

```tsx
import type { Component } from "solid-js";
import { GoogleOAuthProvider } from "../contexts/GoogleOAuthProvider";
import EmailSignup from "../components/EmailSignup";
import GoogleSignupBtn from "../components/GoogleSignupBtn.tsx";

const googleClientId = import.meta.env.VITE_GOOGLE_OAUTH2_CLIENT_ID;
const googleClientNonce = import.meta.env.VITE_GOOGLE_OAUTH2_NONCE;

import styles from "../css/AuthCard.module.css";

const Signup: Component = () => {
  return (
    <div class={styles.AuthCard}>
      <h1>Sign up</h1>
      <EmailSignup />
      <p>Or Continue with:</p>
      <GoogleOAuthProvider
        clientId={googleClientId}
        nonce={googleClientNonce}
      >
        <GoogleSignupBtn />
      </GoogleOAuthProvider>
      <br />
      <br />
      <a href="/login">Already have a Pikoshi account? Log in</a>
    </div>
  );
};

export default Signup;
```

Very similar to our Login View form... let's go ahead and go with the
EmailSignup...what does that comonent look like?:

### The EmailSignup Component

You can find the EmailSignup Component in, you guessed it, the `/src/components`
directory. Let's see what's in this file:

```tsx
import { type Component, createSignal, Show } from "solid-js";

import urls from "../config/urls";
import { validateEmailInput } from "../utils/schema-validators";

const EmailSignup: Component = () => {
  const [email, setEmail] = createSignal<string>("");
  const [message, setMessage] = createSignal<string>("");

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    try {
      validateEmailInput(email());
      const res = await fetch(urls.BACKEND_SIGNUP_EMAIL_ROUTE, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: email() }),
      });
      if (!res.ok) {
        const jsonRes = await res.json();
        throw new Error(jsonRes.message);
      } else {
        const jsonRes = await res.json();
        setMessage(jsonRes.message);
      }
    } catch (err) {
      const error = err as Error;
      console.error("ERROR :=>", error.message);
      setMessage(error.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label for="email-form">email:</label>
        <br />
        <input
          type="email"
          id="email-form"
          placeholder="johndoe@example.com"
          style="text-align: center;"
          value={email()}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <br />
        <br />
        <button type="submit">Continue</button>
      </form>
      <Show when={message().length}>
        <p>{message()}</p>
      </Show>
    </div>
  );
};

export default EmailSignup;
```

Okay! A more in depth chunk of code than the others for sure. So let's break
down what's going on here. We'll forego the initial inputs and take a look at
the declaration of our component:

```tsx
// ...
const EmailSignup: Component = () => {
    const [email, setEmail] = createSignal<string>("");
    const [message, setMessage] = createSignal<string>("");
    // ...
```

Okay, so this is looking a lot like ReactJS's
[useState](https://react.dev/reference/react/useState) hook declarations. And in
essence, they <em>can</em> be used like React's `useState` hooks. There is a lot
going under the hood of `createSignal` that makes them far more performant, but
sufficient to say you can utilize signals <em>almost</em> as if they were the
same. I say <em>almost</em> because, as you'll soon see, there is one small
caveat to that. For now though, let's continue taking a look at our codebase:

```tsx
const handleSubmit = async (e: Event) => {
  e.preventDefault();
  try {
    validateEmailInput(email());
    const res = await fetch(urls.BACKEND_SIGNUP_EMAIL_ROUTE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: email() }),
    });
    if (!res.ok) {
      const jsonRes = await res.json();
      throw new Error(jsonRes.message);
    } else {
      const jsonRes = await res.json();
      setMessage(jsonRes.message);
    }
  } catch (err) {
    const error = err as Error;
    console.error("ERROR :=>", error.message);
    setMessage(error.message);
  }
};
```

Okay...before we get into this function, where is this being called? Let's take
a look at the JSX HTML:

```tsx
// ...
return (
    <div>
        <form onSubmit={handleSubmit}>
            <label for='email-form'>email:</label>
            {/* ... */}
```

Okay, yeah, it's for submitting a form, that figures. Let's go back to the
function now...

```tsx
// ...
const handleSubmit = async (e: Event) => {
    e.preventDefault();
    try {
        validateEmailInput(email());
        // ...
```

Okay... okay, nothing too new here... just classic e.preventDefault() we've seen
a billion times before. Let's move on...

```tsx
validateEmailInput(email());
```

That doesn't look right...in React useState would have been:

```tsx
validateEmailInput(email);
```

I bring this up specifically to point out the most obvious difference between
React's `useState` hook and Solid's `createSignal` function. You <em>must</em>
invoke a signal in order to retrieve it's value, otherwise you will receive an
Accessor related error. This is also apparent when we take a look at the JSX
HTML as well, where we also invoke all signals rather than simply reference
them:

```tsx
return (
  <div>
    <form onSubmit={handleSubmit}>
      <label for="email-form">email:</label>
      <br />
      <input
        type="email"
        id="email-form"
        placeholder="johndoe@example.com"
        style="text-align: center;"
        value={email()}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <br />
      <br />
      <button type="submit">Continue</button>
    </form>
    <Show when={message().length}>
      <p>{message()}</p>
    </Show>
  </div>
);
```

You'll also notice here the use of the `<Show>` control flow statement. This is
semantically different from React's use of ternary conditionals for the same
effect `{? :}`.

**Other SolidJS Features/Quirks:**

I won't go any further on the major semantic differences between the ReactJS and
SolidJS. Sufficient to say that there are equivalents between ReactJS in terms
of hooks. These include SolidJS's
[OnMount](https://docs.solidjs.com/reference/lifecycle/on-mount),
[createEffect](https://docs.solidjs.com/reference/basic-reactivity/create-effect),
[createContext](https://docs.solidjs.com/reference/basic-reactivity/create-effect),
among others. SolidJS also has a more direct and simplified way of dealing with
[Refs](https://docs.solidjs.com/concepts/refs).

SolidJS also utilizes a [For](https://docs.solidjs.com/reference/components/for)
control flow statement as well that is worth investigating.

### Communication with the Backend

Pikoshi holds all references to URLS to the backend in the `src/config/urls.ts`
file. Whenever setting up a `fetch` call to the backend, it is highly encouraged
that you place the URL within an appropriately named urls key, and then provide
the backend URl string there. You can then import it and utilize it in your
`fetch` call. This is meant solely so that it is easy to configure the URLs
(possiblye for later, during production).

### Testing

:construction: NOTE: This section is very incomplete.

At the time of this writing (09/01/2024), there is only one unit test written
for Pikoshi's frontend. This is meant to scaffold off of later on during the
development lifecycle.

That said, I have set up the basic setup to start unit testing using
[Vitest](https://vitest.dev/). You can find the initial code related to testing
in the following files:

- `/vitest.setup.ts`
- `/vitest.config.ts`
- `/src/mocks/handlers.ts`
- `/src/mocks/node.ts`
- `/src/tests/App.test.tsx`

You can currently run the tests by using `bun`:

```sh
bun run test
```

Please note that `bun` also has an underlying test runner, but it does not work
with Pikoshi's current setup. Thusly do NOT use `bun`'s native test runner.

```sh
# Don't do this:
bun test
# Instead do this:
bun run test
```

## Conclusion

At the time of this writing (09/01/2024), Pikoshi is in it's early stages of
development, and thusly there is not a lot of logic going on in either the
Frontend or the Backend other than Authentication logic, and basic image
displaying. That said, I hope that this general overview gave you a good
introduction to the general flow of the Frontend aspect of the application, and
gave you a general idea of the paradigms new developers might have to get used
to using SolidJS.
