import App from '../App.tsx';
import Login from '../views/Login';
import Onboarding from '../views/Onboarding';
import Signup from '../views/Signup';
import TestComponent from '../views/TestComponent';

const routes = [
    {
        path: '/',
        component: App,
    },
    {
        path: '/login',
        component: Login,
    },
    {
        path: '/signup',
        component: Signup,
    },
    {
        path: '/test',
        component: TestComponent,
    },
    {
        path: '/onboarding',
        component: Onboarding,
    },
];

export default routes;
