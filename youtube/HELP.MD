Link YouTube sedikit berbeda, contoh seperti:
https://offers.sheerid.com/youtube/student/?yrdup=https%3A%2F%2Fwww.youtube.com%2F%3Fsld%3Dxxxxxxxxxxxxxxxytpid=premium&ytsku=premium&yrsp=https%3A%2F%2Fwww.youtube.com%2Fpremium%2FstudxxxxxxxxxxxxQQBRgO&euid=230493635&locale=en-US&oid=AI97cxxxxxxxxxxxxxxxxxxxxxNT06Nb5kDzo384b8cAu

Tidak ada informasi programId dan verificationId di URL tersebut, jadi Anda perlu mengambilnya dari request API.

1. Buka DevTools → Network, lalu cari request:
`https://services.sheerid.com/rest/v2/verification/`
2. Ambil programId dari payload request dan verificationId dari response.
3. Susun link manual:
`https://services.sheerid.com/verify/xxx/?verificationId=yyyy`

Keterangan:
- xxx = programId
- yyyy = verificationId
