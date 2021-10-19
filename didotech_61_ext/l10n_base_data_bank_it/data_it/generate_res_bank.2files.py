#!/usr/bin/python

#  # /usr/bin/env python

import codecs
import getopt
import sys

import time

SCRIPT_VERSION = 'v.1'
ENCODING = 'utf-8'


def bank_name(abi):
    with open(abifile) as f:
        for line in f:
            split = line.split(',')
            sabi = split[0].strip('"')
            name = split[1].strip('"')
            if sabi == abi:
                return name.replace('"', '').replace('\r', '').replace('\n', '')
    return ' ??? '


def generate_res_bank(abifile, cabfile, outfile):
    head = '"abi","cab","id","name","street","zip"'
    out = codecs.open(outfile, 'w', encoding=ENCODING)
    out.write(u'{}\n'.format(head))
    tot = sum(1 for line in open(cabfile)) - 1
    startime = time.time()
    count = 0

    with open(cabfile) as f:
        for line in f:
            split = line.replace('"', '').replace('\r', '').replace('\n', '').split(',')
            abi = split[0]
            cab = split[1]
            abiname = bank_name(abi)
            cabname = split[2]
            bankname = abiname
            if cabname:
                bankname = '{} - {}'.format(bankname, cabname)
            # TODO trying to avoid errors
            if len(split) == 6:
                street = '{},{}'.format(split[3], split[4])
                CAP = split[5]
            else:
                street = split[3]
                CAP = split[4]
            outline = '"{}","{}","base.{}{}","{}","{}","{}"'.format(abi, cab, abi, cab, bankname, street, CAP)
            try:
                # CODEC CURRENTLY IS Western 1252 => cp1252
                out.write(u'{}\n'.format(outline.decode('cp1252')))
            except UnicodeDecodeError as e:
                print('** ERROR *** ' + e)

            count += 1
            if count % 5000 == 0:
                currtime = round(time.time() - startime, 2)
                summary = '{}/{}  {} s. ({} min.)'.format(count, tot, currtime, round(currtime / 60, 2))
                print(summary)

    f.close()
    currtime = round(time.time() - startime, 2)
    summary = '=== {}/{}  {} s. ({} min.)\n'.format(count, tot, currtime, round(currtime / 60, 2))
    print(summary)


def usage():
    print '''\nUsage: {name} [-h] -c= -a=
    --help:          show this message
    -c:              cab file (COD_CAB.TXT)
    -a:              abi file (COD_ABI.TXT)
    
You may want to run this:

{name} -c COD_CAB.TXT -a COD_ABI.TXT
    '''.format(name=sys.argv[0])


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:a:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(opts) == 0:
        usage()
        sys.exit(2)

    dbname = ''

    action = ''
    abifile = ''
    cabfile = ''
    outfile = 'res.bank.csv'
    is_simulation = False
    force = False

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt == '-c':
            cabfile = arg
        elif opt == '-a':
            abifile = arg
        else:
            print('sconosciuta combinazione {}-{}', opt, arg)
            usage()
            sys.exit(2)

    if not (abifile and cabfile):
        usage()
    else:
        answer = raw_input('\nATTENZIONE, viene generato (eventualmente sovrascritto) il file {}, continuare? (y/n) '.format(outfile))
        if answer not in ('y', 'yes'):
            print('\nCancellato dall\'utente\n')
            exit(1)

        generate_res_bank(abifile, cabfile, outfile)
        print('File generato.\n')

