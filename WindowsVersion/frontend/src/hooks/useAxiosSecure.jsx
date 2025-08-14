import axios from 'axios'
import { useEffect } from 'react'
import {useAuth} from "../context/AuthContext.jsx";

export const axiosSecure = axios.create({
    baseURL: import.meta.env.VITE_API_URL
})

const useAxiosSecure = () => {
    const { logout } = useAuth()

    useEffect(() => {
        // Request interceptor to add token to every request
        axiosSecure.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('authToken')
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`
                }
                return config
            },
            (error) => {
                return Promise.reject(error)
            }
        )

        // Response interceptor for handling auth errors
        axiosSecure.interceptors.response.use(
            (response) => {
                return response
            },
            async (error) => {
                console.log('error tracked in the interceptor', error.response)
                if (
                    error.response &&
                    (error.response.status === 401 || error.response.status === 403)
                ) {
                    //await logOut()
                }
                return Promise.reject(error)
            }
        )
    }, [logout])

    return axiosSecure
}

export default useAxiosSecure