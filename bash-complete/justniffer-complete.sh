_justniffer_completions() {
    local cur prev opts formats line before_cursor quoted_word
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    


    opts="--help --version -f --filecap -i --interface -l --log-format -a --append-log-format -c --config -U --user -e --execute -p --packet-filter -u --unprintable -t --truncated -x --hex-encode -r --raw -n --not-found -s --max-tcp-streams -d --max-fragmented-ip -F --force-read-pcap"

    # Define format keywords
    formats="%% %- %close.originator %close.time %close.timestamp %close.timestamp2 %connection %connection.time %connection.timestamp %connection.timestamp2 %dest.ip %dest.port %idle.time.0 %idle.time.1 %newline %request %request.grep %request.header %request.header.accept %request.header.accept-charset %request.header.accept-encoding %request.header.accept-language %request.header.authorization %request.header.connection %request.header.content-encoding %request.header.content-language %request.header.content-length %request.header.content-md5 %request.header.cookie %request.header.grep %request.header.host %request.header.keep-alive %request.header.range %request.header.referer %request.header.transfer-encoding %request.header.user-agent %request.header.value %request.header.via %request.line %request.method %request.protocol %request.size %request.time %request.timestamp %request.timestamp2 %request.url %response %response.code %response.grep %response.header %response.header.accept-ranges %response.header.age %response.header.allow %response.header.cache-control %response.header.connection %response.header.content-encoding %response.header.content-language %response.header.content-length %response.header.content-md5 %response.header.content-range %response.header.content-type %response.header.date %response.header.etag %response.header.expires %response.header.grep %response.header.keep-alive %response.header.last-modified %response.header.pragma %response.header.server %response.header.set-cookie %response.header.transfer-encoding %response.header.value %response.header.vary %response.header.via %response.header.www-authenticate %response.line %response.message %response.protocol %response.size %response.time %response.time.begin %response.time.end %response.timestamp %response.timestamp2 %session.requests %session.time %source.ip %source.port %streams %tab"

    # Provide completions
    case "${prev}" in
        --log-format | --append-log-format | -l | -a)
            COMPREPLY=( $(compgen -W "${formats[*]}" -- "$cur") )
            return 0
            ;;
        -i|--interface)
            COMPREPLY=( $(compgen -W "any $(ip link show | awk -F: '/^[0-9]+:/ {print $2}' | tr -d ' ')" -- "${cur}") )
            return 0
            ;;
        -c|--config)
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
        -U|--user)
            COMPREPLY=( $(compgen -u -- "${cur}") )
            return 0
            ;;
        -e|--execute)
            COMPREPLY=( $(compgen -c -- "${cur}") )
            return 0
            ;;
        -p|--packet-filter)
            # Packet filter completions are complex; no completion for now
            ;;
        -n|--not-found)
            # No specific completion
            ;;
        -s|--max-tcp-streams)
            # No specific completion
            ;;
        -d|--max-fragmented-ip)
            # No specific completion
            ;;
        -F|--force-read-pcap)
            # It's a flag; no completion
            ;;
        *)
            COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
            return 0
            ;;
    esac
}

# Register the completion function
complete -F _justniffer_completions justniffer