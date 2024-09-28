import App from "../App.tsx";
import GalleryWrapper from "../views/Gallery";
import Login from "../views/Login";
import Onboarding from "../views/Onboarding";
import Signup from "../views/Signup";
import NotFound from "../views/NotFound";
import ForgotPassword from "../views/ForgotPassword.tsx";

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
        component: GalleryWrapper,
    },
    {
        path: "/*",
        component: NotFound,
    },
    {
        path: "/forgot-password",
        component: ForgotPassword,
    },
];

export default routes;
