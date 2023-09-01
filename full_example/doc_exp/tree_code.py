def with_respect(from_path, to_path):
        # Find their common root
        pc_from = from_path.split("/")
        pc_to = to_path.split("/")
        u = 0
        for k in range(0, max(len(pc_from), len(pc_to))):
            pc_from_v = pc_from[k] if k < len(pc_from) else None
            pc_to_v = pc_to[k] if k < len(pc_to) else None
            if pc_from_v == pc_to_v:
                u += 1
        if u==0:
            return to_path
        else:
            return ("/".join([".."] * (len(pc_from)-u))) + "/" + "/".join(pc_to[u:])

if __name__ == "__main__":
    s_from = "alpha/beta/gamma/delta/epsylon"
    s_to = "alpha/bing/bong/bong"

    q = with_respect(s_from, s_to)

    print(s_from)
    print(s_to)
    print(q)
