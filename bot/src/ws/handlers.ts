import { LocalStorage } from 'node-localstorage';
import { AviatorBotAPI } from "../api/AviatorBotAPI"
import { HTTPStatus } from '../api/constants';


const localStorage = new LocalStorage('./storage');

export async function verifyToken(token: string|null): Promise<any> {
	token = token || localStorage.getItem('token')
	if(token){
		const response = await AviatorBotAPI.requestTokenVerify(token)
		if(response.status == HTTPStatus.OK){
			return {logged: true}
		}
	}
    return {logged: false}
}

export async function login(username: string, password: string): Promise<any> {
	const token = localStorage.getItem('token')
	const refresh = localStorage.getItem('refresh')
	if(token){
        const verify = await verifyToken(token)
        if(verify.logged){
            return {logged: true}
        }
	}else if(refresh){
		const response = await AviatorBotAPI.requestTokenRefresh(refresh)
		if(response.status == HTTPStatus.OK){
			localStorage.setItem('token', response.data.access);
			return {logged: true}
		}
	}
	const response = await AviatorBotAPI.requestLogin(username, password)
	if(response.status !== HTTPStatus.OK){
        if(response.status == HTTPStatus.UNAUTHORIZED){
		    return {logged: false}
        }
        return {error: Object.assign(response, {code: "00"})}
        
	}
	localStorage.setItem('token', response.data.access);
	localStorage.setItem('refresh', response.data.refresh);
	return {logged: true}
}