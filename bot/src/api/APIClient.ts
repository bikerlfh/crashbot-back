import axios, { AxiosResponse, AxiosError, AxiosRequestConfig } from 'axios';

class ApiClient {
	private readonly baseUrl: string;

	constructor(baseUrl: string) {
			this.baseUrl = baseUrl;
	}

	public async get<T>(path: string, config?: AxiosRequestConfig): Promise<T> {
		return axios
			.get(`${this.baseUrl}${path}`, config)
			.then((response: AxiosResponse) => response.data)
			.catch((error: AxiosError) => {
				throw new Error(`Failed to GET ${path}. ${error}`);
			});
	}

	public async post<T>(path: string, data: any, config?: AxiosRequestConfig): Promise<T> {
		return axios
			.post(`${this.baseUrl}${path}`, data, config)
			.then((response: AxiosResponse) => response.data)
			.catch((error: AxiosError) => {
				throw new Error(`Failed to POST ${path}. ${error}`);
			});
	}

	public async put<T>(path: string, data: any, config?: AxiosRequestConfig): Promise<T> {
		return axios
			.put(`${this.baseUrl}${path}`, data, config)
			.then((response: AxiosResponse) => response.data)
			.catch((error: AxiosError) => {
				throw new Error(`Failed to PUT ${path}. ${error}`);
			});
	}

	public async patch<T>(path: string, data: any, config?: AxiosRequestConfig): Promise<T> {
		return axios
			.patch(`${this.baseUrl}${path}`, data, config)
			.then((response: AxiosResponse) => response.data)
			.catch((error: AxiosError) => {
				throw new Error(`Failed to PATCH ${path}. ${error}`);
			});
	}

	public async delete<T>(path: string, config?: AxiosRequestConfig): Promise<T> {
		return axios
			.delete(`${this.baseUrl}${path}`, config)
			.then((response: AxiosResponse) => response.data)
			.catch((error: AxiosError) => {
				throw new Error(`Failed to DELETE ${path}. ${error}`);
			});
	}
}
