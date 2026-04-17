export const token = () => {
    return {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
}
