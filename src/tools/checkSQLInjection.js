import axios from 'axios';

export default async function checkSQLInjection(url = "", params = [{ name: "id", value: "123"}]) {
  const fullUrl = `${url}?${params.map(param => param.name + "=" + encodeURIComponent(param.value)).join('&')}`;
  
  try {
    const response = await axios.get(fullUrl);
    if (response.data.toLowerCase().includes('sql') || response.data.toLowerCase().includes('error')) {
      return {
        type: "success",
        message: "Possible SQL Injection vulnerability found!"
      }
    } else {
      return {
        type: "warning",
        message: "No SQL Injection vulnerabilities detected."
      }
    }
  } catch (error) {
    return {
      type: "error",
      message: `Error on request: ${error.message}`
    }
  }
}