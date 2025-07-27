import { useFrappeAuth, useFrappeGetDoc } from "frappe-react-sdk"


export default function Test() {
    const auth = useFrappeAuth()
    const {data: user} = useFrappeGetDoc("User", auth?.currentUser ?? "")
    console.log(user)
  return (
    <div>
      <div>user : {JSON.stringify(user)}</div>
    </div>
  )
}
