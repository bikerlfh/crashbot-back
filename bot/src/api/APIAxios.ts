import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import {APIUrl, HTTPStatus} from './constants';
import { LocalStorage } from 'node-localstorage';

export class ApiService {
	private readonly httpClient: AxiosInstance;
  	private readonly localStorage: LocalStorage;

	constructor() {
		const baseURL = APIUrl;
		this.httpClient = axios.create({
			baseURL,
			headers: {
				'Content-Type': 'application/json',
			},
		});
		// Creamos una instancia del almacenamiento persistente y lo asignamos a una variable de clase
		this.localStorage = new LocalStorage('./storage');
	}
	private mapError(error: AxiosError): any{
		const response = {
			status: error.response?.status,
			statusText: error.response?.statusText,
			data: error.response?.data
		}
		return response
	}
	private mapResponse<T>(response: AxiosResponse<T>): any {
		if(response.status === HTTPStatus.INTERNAL_ERROR){
			throw "internal server error"
		}
		const res = {
			status: response.status,
			data: response.data
		}
		return res;
	}



	public async get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>|any> {
		return this.httpClient.get<T>(url, this.addAuthHeader(config)).then((res) => {
			return this.mapResponse(res)
		}).catch((res) => {
			return this.mapError(res)
		});
	}

	public async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>|any> {
		return this.httpClient.post(url, data, this.addAuthHeader(config)).then((res) => {
			return this.mapResponse(res)
		}).catch((res) => {
			return this.mapError(res)
		});
	}

	public async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>|any> {
		return this.httpClient.put<T>(url, data, this.addAuthHeader(config)).then((res) => {
			return this.mapResponse(res)
		}).catch((res) => {
			return this.mapError(res)
		});
	}

	public async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>|any> {
		return this.httpClient.patch<T>(url, data, this.addAuthHeader(config)).then((res) => {
			return this.mapResponse(res)
		}).catch((res) => {
			return this.mapError(res)
		});
	}

	public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>|any> {
		return this.httpClient.delete<T>(url, this.addAuthHeader(config)).then((res) => {
			return this.mapResponse(res)
		}).catch((res) => {
			return this.mapError(res)
		});
	}

	private addAuthHeader(config?: AxiosRequestConfig): AxiosRequestConfig {
		const token = this.localStorage.getItem('token');

		if (!token) {
			return config || {};
		}

		const headers = {
			...config?.headers,
			Authorization: `token ${token}`,
		};

		return { ...config, headers };
	}
}
