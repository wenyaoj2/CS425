import socket


class get_ip:

    linklist = ["sp19-cs425-g34-01.cs.illinois.edu",
                "sp19-cs425-g34-02.cs.illinois.edu",
                "sp19-cs425-g34-03.cs.illinois.edu",
                "sp19-cs425-g34-04.cs.illinois.edu",
                "sp19-cs425-g34-05.cs.illinois.edu",
                "sp19-cs425-g34-06.cs.illinois.edu",
                "sp19-cs425-g34-07.cs.illinois.edu",
                "sp19-cs425-g34-08.cs.illinois.edu",
                "sp19-cs425-g34-09.cs.illinois.edu",
                "sp19-cs425-g34-10.cs.illinois.edu"]

    def __init__(self):
        pass

    def get_ip_list(self):
        ip_list = []
        for url in self.linklist:
            ip_list.append(socket.gethostbyname(url))
        return ip_list

    def get_url_list(self):
        return self.linklist