import App from '../App.tsx';
import TestComponent from '../views/TestComponent';
import Login from '../views/Login';
import Signup from '../views/Signup';

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
];

export default routes;
