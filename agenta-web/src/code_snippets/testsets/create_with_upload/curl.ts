export default function cURLCode(uri: string, appName: string): string {
    return `curl -X POST ${uri} \\
-H 'Content-Type: multipart/form-data' \\
-F 'file=@/path/to/your/file.csv' \\
-F 'testset_name=your_testset_name' \\
-F 'app_name=${appName}'
`
}
