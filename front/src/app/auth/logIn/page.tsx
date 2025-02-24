import { FormEvent } from 'react'
import { useRouter } from 'next/router'
import { logInRequest } from '@/app/request'

export default function LoginPage() {
  const router = useRouter()

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const formData = new FormData(event.currentTarget)
    const userName = formData.get('userName')?.toString()
    const password = formData.get('password')?.toString()

    const response = await logInRequest(userName, password);


    if (response.ok) {
      router.push('/')
    } else {
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="userName" placeholder="userName" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  )
}
